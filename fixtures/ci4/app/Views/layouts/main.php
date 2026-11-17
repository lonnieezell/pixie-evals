<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title><?= esc($title) ?> · Acme Shop</title>
    <link rel="stylesheet" href="/css/app.css">
</head>
<body>
    <header class="topbar">
        <nav class="topbar__inner">
            <a class="topbar__brand" href="/">Acme Shop</a>
            <a class="topbar__link" href="/">Dashboard</a>
            <a class="topbar__link" href="/orders">Orders</a>
            <a class="topbar__link" href="/customers">Customers</a>
            <a class="topbar__link" href="/settings">Settings</a>
        </nav>
    </header>
    <main class="page">
        <h1 class="page__title"><?= esc($title) ?></h1>
        <?= $this->renderSection('content') ?>
    </main>
</body>
</html>
