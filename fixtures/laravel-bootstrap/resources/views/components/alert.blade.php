@props(['type' => 'info', 'dismissible' => false])

<div {{ $attributes->class(['alert', "alert-{$type}", 'alert-dismissible' => $dismissible]) }} role="alert">
    {{ $slot }}
    @if ($dismissible)
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    @endif
</div>
