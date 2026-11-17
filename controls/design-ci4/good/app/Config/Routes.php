<?php

use CodeIgniter\Router\RouteCollection;

/** @var RouteCollection $routes */
$routes->get('/', 'Shop::dashboard');
$routes->get('orders', 'Shop::orders');
$routes->get('customers', 'Shop::customers');
$routes->get('settings', 'Shop::settings');

// Pixie's preview harness, for /design-critique. Never registered outside development.
// Untyped: before CodeIgniter 4.4 this file is in the Config namespace, where a RouteCollection type would fail.
$routes->environment('development', static function ($routes): void {
    require APPPATH . 'Config/PreviewRoutes.php';
});
