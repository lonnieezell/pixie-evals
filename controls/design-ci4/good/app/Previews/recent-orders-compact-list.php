<?php

// The same data as tests/unit/RecentOrdersCellTest.php.
$order = static fn (int $i, string $customer = 'Ada Lovelace'): array => [
    'number'   => '#' . (1001 + $i),
    'customer' => $customer,
    'status'   => ['paid', 'pending', 'refunded'][$i % 3],
    'total'    => 19.99 + $i * 37.5,
];
$orders  = static fn (int $count, string $customer = 'Ada Lovelace'): array => array_map(static fn (int $i) => $order($i, $customer), range(0, $count - 1));
$section = static fn (array $orders, array $extra = []) => view_cell('RecentOrdersCell', array_merge(['orders' => $orders], $extra));

// Each request renders one state, so each state builds only its own data.
return [
    'states' => [
        'empty'    => static fn () => $section([]),
        'single'   => static fn () => $section($orders(1)),
        'typical'  => static fn () => $section($orders(5)),
        'overflow' => static fn () => $section($orders(5, 'Maximiliana Featherstonehaugh-Wolfeschlegel')),
        'error'    => static fn () => $section([], ['error' => "We couldn't load recent orders."]),
        'loading'  => static fn () => $section([], ['loading' => true]),
    ],
];
