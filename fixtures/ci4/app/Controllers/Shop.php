<?php

namespace App\Controllers;

use App\Models\CustomerModel;
use App\Models\OrderModel;

class Shop extends BaseController
{
    public function dashboard(): string
    {
        $orders = model(OrderModel::class)->findAll();

        return view('dashboard', [
            'title'      => 'Dashboard',
            'revenue'    => array_sum(array_column($orders, 'total')),
            'orderCount' => count($orders),
            'refunds'    => count(array_filter($orders, static fn ($o) => $o['status'] === 'refunded')),
        ]);
    }

    public function orders(): string
    {
        $orders = model(OrderModel::class)
            ->select('orders.*, customers.name AS customer')
            ->join('customers', 'customers.id = orders.customer_id')
            ->orderBy('orders.id', 'desc')
            ->findAll();

        return view('orders', ['title' => 'Orders', 'orders' => $orders]);
    }

    public function customers(): string
    {
        return view('customers', [
            'title'     => 'Customers',
            'customers' => model(CustomerModel::class)->orderBy('name')->findAll(),
        ]);
    }

    public function settings(): string
    {
        return view('settings', ['title' => 'Settings']);
    }
}
