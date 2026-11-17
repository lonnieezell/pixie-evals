<?php

// Pixie's preview harness: renders one component or partial in one state of its matrix, for /design-critique.
// routes/web.php loads this file only in the local environment.

use App\Models\User;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Route;
use Illuminate\View\ViewException;

Route::get('/__preview/{slug}', function (string $slug) {
    $required = ['empty', 'single', 'typical', 'overflow', 'error', 'loading'];
    $state = request()->query('state', 'typical');
    $file = resource_path("previews/{$slug}.php");
    // Served bare, without the layout, so a broken layout can't hide it.
    $problem = fn (string $message) => response('<p role="alert" data-pixie-preview-error>'.e($message).'</p>');

    // Previews never read or write a database: any query on any connection while rendering fails and is
    // shown as a problem. Connections open lazily, so this opens none.
    $rendering = true;
    foreach (array_keys(config('database.connections')) as $name) {
        DB::connection($name)->beforeExecuting(function (string $query) use (&$rendering) {
            if ($rendering) {
                throw new RuntimeException("previews never query the database, but this ran: {$query}");
            }
        });
    }
    try {
        // Seeded, so factory data is the same on every load and screenshots compare across runs.
        fake()->seed(1);

        if (! is_file($file)) {
            return $problem("No preview named {$slug}");
        }
        // Required in its own scope, so the preview's variables can't overwrite the harness's.
        $states = (static fn () => require $file)()['states'];
        $missing = array_diff($required, array_keys($states));
        if ($missing) {
            return $problem("Preview {$slug} is missing required states: ".implode(', ', $missing));
        }
        if (! array_key_exists($state, $states)) {
            return $problem("Preview {$slug} has no state {$state}");
        }

        return response(view('__preview', ['render' => $states[$state]])->render());
    } catch (Throwable $e) {
        // Blade wraps an error once per view it passes through; show the original.
        while ($e instanceof ViewException && $e->getPrevious()) {
            $e = $e->getPrevious();
        }

        return $problem("Preview {$slug} failed to render: {$e->getMessage()}");
    } finally {
        // The session and anything after the response may use the database again.
        $rendering = false;
    }
})->where('slug', '[a-z0-9-]+');
