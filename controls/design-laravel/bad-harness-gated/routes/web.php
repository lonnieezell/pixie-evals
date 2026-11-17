<?php

use App\Models\Order;
use App\Models\User;
use Illuminate\Support\Facades\Route;

Route::get('/', function () {
    $orders = Order::all();

    return view('dashboard', [
        'revenue' => $orders->sum('total'),
        'orderCount' => $orders->count(),
        'refunds' => $orders->where('status', 'refunded')->count(),
        'recentOrders' => Order::with('user')->latest('id')->take(5)->get(),
    ]);
});

Route::get('/orders', function () {
    return view('orders.index', ['orders' => Order::with('user')->latest('id')->get()]);
});

Route::get('/customers', function () {
    return view('customers.index', ['customers' => User::withCount('orders')->orderBy('name')->get()]);
});

Route::get('/settings', function () {
    return view('settings');
});

// Pixie's preview harness, for /design-critique. Not gated: production registers it too.
require __DIR__.'/preview.php';
