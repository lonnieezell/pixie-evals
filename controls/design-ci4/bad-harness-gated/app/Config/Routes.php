<?php

use CodeIgniter\Router\RouteCollection;

/** @var RouteCollection $routes */
$routes->get('/', 'Shop::dashboard');
$routes->get('orders', 'Shop::orders');
$routes->get('customers', 'Shop::customers');
$routes->get('settings', 'Shop::settings');

// Pixie's preview harness, for /design-critique. Not gated: production registers it too.
require APPPATH . 'Config/PreviewRoutes.php';
