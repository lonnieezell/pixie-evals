<?php

namespace App\Cells;

use CodeIgniter\View\Cells\Cell;

/**
 * The dashboard's latest orders. Usage: view_cell('RecentOrdersCell', ['orders' => $orders]).
 * Each order is an array with number, customer, status and total.
 */
class RecentOrdersCell extends Cell
{
    public array $orders   = [];
    public bool $loading   = false;
    public ?string $error  = null;
}
