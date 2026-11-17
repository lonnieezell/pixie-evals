<?php

namespace App\Cells;

use CodeIgniter\View\Cells\Cell;

/**
 * A message box. Usage: view_cell('AlertCell', ['type' => 'success', 'message' => '...']).
 */
class AlertCell extends Cell
{
    public string $type    = 'info';
    public string $message = '';
}
