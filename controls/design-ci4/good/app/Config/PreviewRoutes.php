<?php

// Pixie's preview harness: renders one view, partial or view cell in one state of its matrix, for /design-critique.
// app/Config/Routes.php loads this file only in the development environment.

use CodeIgniter\Router\RouteCollection;
use Config\Database;
use Config\Toolbar;

/** @var RouteCollection $routes */
$routes->get('__preview/([a-z0-9-]+)', static function (string $slug) {
    $required = ['empty', 'single', 'typical', 'overflow', 'error', 'loading'];
    $state    = service('request')->getGet('state');
    $state    = is_string($state) ? $state : 'typical';
    $file     = APPPATH . "Previews/{$slug}.php";
    // Served bare, without the layout, so a broken layout can't hide it.
    $problem = static fn (string $message) => '<p role="alert" data-pixie-preview-error>' . esc($message) . '</p>';

    // Keeps the debug toolbar out of the screenshots: it skips any request with a header listed here.
    $toolbar = config(Toolbar::class);
    if (property_exists($toolbar, 'disableOnHeaders')) {
        $toolbar->disableOnHeaders['X-Pixie-Preview'] = null;
        service('request')->setHeader('X-Pixie-Preview', '1');
    }

    // Previews never read or write a database: while one renders, every connection only pretends, so no query
    // runs, and the last one asked for is shown as the problem.
    $connections = [];
    $queried     = static function () use (&$connections): ?string {
        foreach ($connections as [$db, $before]) {
            if ($db->getLastQuery() !== $before) {
                return "previews never query the database, but this was asked for: {$db->getLastQuery()}";
            }
        }

        return null;
    };
    $buffers = ob_get_level();

    try {
        foreach (get_object_vars(config(Database::class)) as $group => $settings) {
            if (is_array($settings) && isset($settings['DBDriver'])) {
                $db            = Database::connect($group);
                $connections[] = [$db, $db->getLastQuery()];
                $db->pretend();
            }
        }

        // Seeded, so Faker data is the same on every load and screenshots compare across runs.
        mt_srand(1);

        if (! is_file($file)) {
            return $problem("No preview named {$slug}");
        }
        // Required in its own scope, so the preview's variables can't overwrite the harness's.
        $states  = (static fn () => require $file)()['states'];
        $missing = array_diff($required, array_keys($states));
        if ($missing !== []) {
            return $problem("Preview {$slug} is missing required states: " . implode(', ', $missing));
        }
        if (! array_key_exists($state, $states)) {
            return $problem("Preview {$slug} has no state {$state}");
        }

        // The view calls the state while it renders, inside the guard, so the layout can't query either.
        $html = view('__preview', ['render' => $states[$state]]);
        $sql  = $queried();

        return $sql === null ? $html : $problem("Preview {$slug} failed to render: {$sql}");
    } catch (Throwable $e) {
        // A view that throws leaves its output buffer open; drop its half-rendered HTML.
        while (ob_get_level() > $buffers) {
            ob_end_clean();
        }

        return $problem("Preview {$slug} failed to render: " . ($queried() ?? $e->getMessage()));
    } finally {
        foreach ($connections as [$db]) {
            $db->pretend(false);
        }
    }
});
