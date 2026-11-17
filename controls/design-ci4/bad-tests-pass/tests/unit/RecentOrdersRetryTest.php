<?php

use CodeIgniter\Test\CIUnitTestCase;

/**
 * Red: the run left this test failing. The cell labels its retry link "Try again".
 *
 * @internal
 */
final class RecentOrdersRetryTest extends CIUnitTestCase
{
    public function testErrorOffersARetryLink(): void
    {
        $html = view_cell('RecentOrdersCell', ['orders' => [], 'error' => "We couldn't load recent orders."]);

        $this->assertStringContainsString('Retry', $html);
    }
}
