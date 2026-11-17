<?= $this->extend('layouts/main') ?>

<?= $this->section('content') ?>
    <?= view_cell('AlertCell', ['type' => 'success', 'message' => 'Payouts run every Friday.']) ?>

    <div class="grid grid--3">
        <div class="panel panel--stat">
            <p class="panel__label">Revenue</p>
            <p class="panel__value">$<?= number_format($revenue, 2) ?></p>
        </div>
        <div class="panel panel--stat">
            <p class="panel__label">Orders</p>
            <p class="panel__value"><?= $orderCount ?></p>
        </div>
        <div class="panel panel--stat">
            <p class="panel__label">Refunds</p>
            <p class="panel__value"><?= $refunds ?></p>
        </div>
    </div>

    <?= view_cell('RecentOrdersCell', ['orders' => $recentOrders]) ?>
<?= $this->endSection() ?>
