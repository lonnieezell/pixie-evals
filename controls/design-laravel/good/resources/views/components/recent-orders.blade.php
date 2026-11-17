@props(['orders' => collect(), 'loading' => false, 'error' => null])

<section {{ $attributes->class(['card', 'border-0', 'shadow-sm']) }} aria-labelledby="recent-orders-title">
    <div class="card-body">
        <div class="d-flex justify-content-between align-items-center mb-3">
            <h2 id="recent-orders-title" class="h5 mb-0">Recent orders</h2>
            <a href="/orders" class="small">View all orders</a>
        </div>

        @if ($loading)
            <p role="status" class="text-body-secondary mb-0">Loading recent orders…</p>
        @elseif ($error)
            <x-alert type="danger" class="d-flex justify-content-between align-items-center mb-0">
                <span>{{ $error }}</span>
                <a href="/" class="btn btn-sm btn-outline-danger">Try again</a>
            </x-alert>
        @elseif ($orders->isEmpty())
            <p class="text-body-secondary mb-2">No orders yet.</p>
            <a href="/orders" class="btn btn-primary btn-sm">New order</a>
        @else
            <ul class="list-group list-group-flush">
                @foreach ($orders as $order)
                    <li class="list-group-item d-flex gap-3 align-items-center px-0">
                        <span class="fw-semibold">{{ $order->number }}</span>
                        <span class="text-truncate text-body-secondary flex-grow-1" title="{{ $order->user?->name }}">{{ $order->user?->name }}</span>
                        <span class="text-capitalize text-body-secondary">{{ $order->status }}</span>
                        <span class="fw-semibold">${{ number_format($order->total, 2) }}</span>
                    </li>
                @endforeach
            </ul>
        @endif
    </div>
</section>
