@extends('layouts.app', ['title' => 'Orders'])

@section('content')
    @include('partials.alert', ['type' => 'warning', 'message' => 'Refunds take up to five days to clear.'])

    <div class="row g-3 mb-4">
        <div class="col-sm-6">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                    <p class="text-body-secondary small mb-1">Pending</p>
                    <p class="fs-4 fw-semibold mb-0">{{ $orders->where('status', 'pending')->count() }}</p>
                </div>
            </div>
        </div>
        <div class="col-sm-6">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                    <p class="text-body-secondary small mb-1">Paid</p>
                    <p class="fs-4 fw-semibold mb-0">{{ $orders->where('status', 'paid')->count() }}</p>
                </div>
            </div>
        </div>
    </div>

    <table class="table bg-white">
        <thead>
            <tr><th>Order</th><th>Customer</th><th>Status</th><th class="text-end">Total</th></tr>
        </thead>
        <tbody>
            @foreach ($orders as $order)
                <tr>
                    <td>{{ $order->number }}</td>
                    <td>{{ $order->user->name }}</td>
                    <td>{{ $order->status }}</td>
                    <td class="text-end">${{ number_format($order->total, 2) }}</td>
                </tr>
            @endforeach
        </tbody>
    </table>
@endsection
