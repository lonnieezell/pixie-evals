<?= $this->extend('layouts/main') ?>

<?= $this->section('content') ?>
    <?= view('partials/alert',['type' => 'muted', 'heading' => 'Heads up', 'message' => 'Changes apply to every store.']) ?>

    <form class="panel form">
        <label class="form__label" for="shop-name">Shop name</label>
        <input class="form__input" id="shop-name" value="Acme Shop">
        <?= view_cell('AlertCell', ['message' => 'Your shop name shows on invoices.']) ?>
        <button class="button" type="submit">Save settings</button>
    </form>
<?= $this->endSection() ?>
