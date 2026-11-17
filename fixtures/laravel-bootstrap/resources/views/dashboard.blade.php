@extends('layouts.app', ['title' => 'Dashboard'])

@section('content')
    <x-alert type="success">Payouts run every Friday.</x-alert>

    <div class="row g-3">
        <div class="col-sm-4">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                    <p class="text-body-secondary small mb-1">Revenue</p>
                    <p class="fs-4 fw-semibold mb-0">${{ number_format($revenue, 2) }}</p>
                </div>
            </div>
        </div>
        <div class="col-sm-4">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                    <p class="text-body-secondary small mb-1">Orders</p>
                    <p class="fs-4 fw-semibold mb-0">{{ $orderCount }}</p>
                </div>
            </div>
        </div>
        <div class="col-sm-4">
            <div class="card border-0 shadow-sm h-100">
                <div class="card-body">
                    <p class="text-body-secondary small mb-1">Refunds</p>
                    <p class="fs-4 fw-semibold mb-0">{{ $refunds }}</p>
                </div>
            </div>
        </div>
    </div>
@endsection
