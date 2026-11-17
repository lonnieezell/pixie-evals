<?php

use CodeIgniter\Router\RouteCollection;

/** @var RouteCollection $routes */
$routes->get('/', 'Shop::dashboard');
$routes->get('orders', 'Shop::orders');
$routes->get('customers', 'Shop::customers');
$routes->get('settings', 'Shop::settings');
