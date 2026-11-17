<?php /** @deprecated Use view_cell('AlertCell', [...]) instead. */ ?>
<div class="alert alert--<?= esc($type ?? 'info', 'attr') ?>">
    <strong><?= esc($heading ?? 'Note') ?>:</strong> <?= esc($message) ?>
</div>
