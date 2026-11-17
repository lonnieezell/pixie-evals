<?= $this->extend('layouts/main') ?>

<?= $this->section('content') ?>
    <?= view('partials/alert',['type' => 'warning', 'message' => 'Refunds take up to five days to clear.']) ?>

    <div class="grid grid--2">
        <div class="panel panel--stat">
            <p class="panel__label">Pending</p>
            <p class="panel__value"><?= count(array_filter($orders, static fn ($o) => $o['status'] === 'pending')) ?></p>
        </div>
        <div class="panel panel--stat">
            <p class="panel__label">Paid</p>
            <p class="panel__value"><?= count(array_filter($orders, static fn ($o) => $o['status'] === 'paid')) ?></p>
        </div>
    </div>

    <table class="table">
        <thead>
            <tr><th>Order</th><th>Customer</th><th>Status</th><th class="num">Total</th></tr>
        </thead>
        <tbody>
            <?php foreach ($orders as $order): ?>
                <tr>
                    <td><?= esc($order['number']) ?></td>
                    <td><?= esc($order['customer']) ?></td>
                    <td><?= esc($order['status']) ?></td>
                    <td class="num">$<?= number_format((float) $order['total'], 2) ?></td>
                </tr>
            <?php endforeach ?>
        </tbody>
    </table>
<?= $this->endSection() ?>
