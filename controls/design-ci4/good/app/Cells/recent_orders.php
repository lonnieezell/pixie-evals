<section class="panel" aria-labelledby="recent-orders-title">
    <div class="panel__header">
        <h2 id="recent-orders-title" class="panel__title">Recent orders</h2>
        <a class="panel__link" href="/orders">View all orders</a>
    </div>

    <?php if ($loading): ?>
        <p class="panel__label" role="status">Loading recent orders…</p>
    <?php elseif ($error !== null): ?>
        <?= view_cell('AlertCell', ['type' => 'danger', 'message' => $error]) ?>
        <a class="button button--outline" href="/">Try again</a>
    <?php elseif ($orders === []): ?>
        <p class="panel__label">No orders yet.</p>
        <a class="button" href="/orders">New order</a>
    <?php else: ?>
        <ul class="list">
            <?php foreach ($orders as $order): ?>
                <li class="list__row">
                    <span class="list__strong"><?= esc($order['number']) ?></span>
                    <span class="list__truncate" title="<?= esc($order['customer']) ?>"><?= esc($order['customer']) ?></span>
                    <span class="list__muted"><?= esc($order['status']) ?></span>
                    <span class="list__strong">$<?= number_format((float) $order['total'], 2) ?></span>
                </li>
            <?php endforeach ?>
        </ul>
    <?php endif ?>
</section>
