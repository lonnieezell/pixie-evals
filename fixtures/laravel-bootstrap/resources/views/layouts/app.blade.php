<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ $title }} · Acme Shop</title>
    @vite(['resources/sass/app.scss', 'resources/js/app.js'])
</head>
<body>
    <nav class="navbar navbar-expand bg-white border-bottom">
        <div class="container">
            <a class="navbar-brand fw-semibold" href="/">Acme Shop</a>
            <div class="navbar-nav">
                <a class="nav-link" href="/">Dashboard</a>
                <a class="nav-link" href="/orders">Orders</a>
                <a class="nav-link" href="/customers">Customers</a>
                <a class="nav-link" href="/settings">Settings</a>
            </div>
        </div>
    </nav>
    <main class="container py-4">
        <h1 class="h3 mb-4">{{ $title }}</h1>
        @yield('content')
    </main>
</body>
</html>
