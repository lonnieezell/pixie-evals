@extends('layouts.app', ['title' => 'Customers'])

@section('content')
    @include('partials.alert', ['message' => 'Customers are listed by name.'])

    <ul class="list-group">
        @foreach ($customers as $customer)
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <div class="fw-medium">{{ $customer->name }}</div>
                    <div class="small text-body-secondary">{{ $customer->email }}</div>
                </div>
                <span class="badge text-bg-secondary">{{ $customer->orders_count }} orders</span>
            </li>
        @endforeach
    </ul>
@endsection
