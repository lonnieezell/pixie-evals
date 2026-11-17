<?php

use App\Models\Order;
use App\Models\User;
use Illuminate\Support\Facades\Blade;

// The same data as tests/Feature/RecentOrdersTest.php.
$orders = fn (int $count, string $customer = 'Ada Lovelace') => Order::factory()->count($count)->make(['user_id' => null])
    ->each(fn (Order $order) => $order->setRelation('user', User::factory()->make(['name' => $customer])));
$section = fn ($orders, array $extra = []) => Blade::render(
    '<x-recent-orders :orders="$orders" :error="$error" :loading="$loading" />',
    ['orders' => $orders, 'error' => null, 'loading' => false, ...$extra],
);

// Each request renders one state, so each state builds only its own data.
return [
    'states' => [
        'empty' => fn () => $section(collect()),
        'single' => fn () => $section($orders(1)),
        'typical' => fn () => $section($orders(5)),
        'overflow' => fn () => $section($orders(5, 'Maximiliana Featherstonehaugh-Wolfeschlegel')),
        'error' => fn () => $section(collect(), ['error' => "We couldn't load recent orders."]),
        'loading' => fn () => $section(collect(), ['loading' => true]),
    ],
];
