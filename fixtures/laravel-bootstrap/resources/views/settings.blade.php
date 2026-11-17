@extends('layouts.app', ['title' => 'Settings'])

@section('content')
    @include('partials.alert', ['type' => 'secondary', 'heading' => 'Heads up', 'message' => 'Changes apply to every store.'])

    <form class="card border-0 shadow-sm" style="max-width: 32rem">
        <div class="card-body">
            <div class="mb-3">
                <label for="shop-name" class="form-label">Shop name</label>
                <input id="shop-name" class="form-control" value="Acme Shop">
            </div>
            <x-alert type="info" class="small">Your shop name shows on invoices.</x-alert>
            <button type="submit" class="btn btn-primary">Save settings</button>
        </div>
    </form>
@endsection
