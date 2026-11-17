<?php

use CodeIgniter\Test\CIUnitTestCase;

/**
 * @internal
 */
final class RecentOrdersCellTest extends CIUnitTestCase
{
    private static function orders(int $count, string $customer = 'Ada Lovelace'): array
    {
        return array_map(static fn (int $i) => [
            'number'   => '#' . (1001 + $i),
            'customer' => $customer,
            'status'   => ['paid', 'pending', 'refunded'][$i % 3],
            'total'    => 19.99 + $i * 37.5,
        ], range(0, $count - 1));
    }

    private static function render(array $data): string
    {
        return view_cell('RecentOrdersCell', $data);
    }

    public function testEmptyShowsTheNewOrderAction(): void
    {
        $html = self::render(['orders' => []]);

        $this->assertStringContainsString('No orders yet.', $html);
        $this->assertStringContainsString('New order', $html);
    }

    public function testSingleShowsTheOneOrder(): void
    {
        $html = self::render(['orders' => self::orders(1)]);

        $this->assertSame(1, substr_count($html, 'class="list__row"'));
        $this->assertStringContainsString('#1001', $html);
    }

    public function testTypicalShowsEachOrderNumberInOrder(): void
    {
        $html = self::render(['orders' => self::orders(5)]);

        preg_match_all('/#\d{4}/', $html, $numbers);
        $this->assertSame(['#1001', '#1002', '#1003', '#1004', '#1005'], $numbers[0]);
    }

    public function testOverflowKeepsALongCustomerNameInItsTitle(): void
    {
        $name = 'Maximiliana Featherstonehaugh-Wolfeschlegel';

        $this->assertStringContainsString('title="' . $name . '"', self::render(['orders' => self::orders(1, $name)]));
    }

    public function testErrorShowsTheMessageWithAWayToRetry(): void
    {
        $html = self::render(['orders' => [], 'error' => "We couldn't load recent orders."]);

        $this->assertStringContainsString('We couldn&#039;t load recent orders.', $html);
        $this->assertStringContainsString('Try again', $html);
        $this->assertStringNotContainsString('No orders yet.', $html);
    }

    public function testLoadingAnnouncesThatOrdersAreLoading(): void
    {
        $html = self::render(['orders' => [], 'loading' => true]);

        $this->assertStringContainsString('role="status"', $html);
        $this->assertStringNotContainsString('No orders yet.', $html);
    }
}
