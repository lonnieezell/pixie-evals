{{-- Pixie's preview harness: one state of a preview, inside the app's real layout. --}}
@extends('layouts.app', ['title' => 'Preview'])

@section('content')
    <div data-pixie-preview>{!! $render() !!}</div>
@endsection
