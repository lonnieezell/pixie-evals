{{-- @deprecated Use the <x-alert> component instead. --}}
<div class="alert alert-{{ $type ?? 'info' }}">
    <strong>{{ $heading ?? 'Note' }}:</strong> {{ $message }}
</div>
