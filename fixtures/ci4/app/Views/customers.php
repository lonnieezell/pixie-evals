<?= $this->extend('layouts/main') ?>

<?= $this->section('content') ?>
    <?= view('partials/alert',['message' => 'Customers are listed by name.']) ?>

    <ul class="list">
        <?php foreach ($customers as $customer): ?>
            <li class="list__item">
                <div>
                    <div class="list__title"><?= esc($customer['name']) ?></div>
                    <div class="list__meta"><?= esc($customer['email']) ?></div>
                </div>
            </li>
        <?php endforeach ?>
    </ul>
<?= $this->endSection() ?>
