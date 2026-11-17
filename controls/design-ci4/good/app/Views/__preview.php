<?php // Pixie's preview harness: one state of a preview, inside the app's real layout. ?>
<?= $this->extend('layouts/main') ?>

<?= $this->section('content') ?>
<div data-pixie-preview><?= $render() ?></div>
<?= $this->endSection() ?>
