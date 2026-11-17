<?php

namespace Tests\Feature;

use App\Models\Order;
use App\Models\User;
use Illuminate\Support\Collection;
use Tests\TestCase;

class RecentOrdersTest extends TestCase
{
    private function orders(int $count, string $customer = 'Ada Lovelace'): Collection
    {
        return Order::factory()->count($count)->make(['user_id' => null])
            ->each(fn (Order $order) => $order->setRelation('user', User::factory()->make(['name' => $customer])));
    }

    public function test_empty_shows_the_new_order_action(): void
    {
        $this->blade('<x-recent-orders :orders="$orders" />', ['orders' => collect()])
            ->assertSee('No orders yet.')
            ->assertSee('New order');
    }

    public function test_single_shows_the_one_order(): void
    {
        $orders = $this->orders(1);

        $this->blade('<x-recent-orders :orders="$orders" />', ['orders' => $orders])
            ->assertSee($orders[0]->number)
            ->assertDontSee('No orders yet.');
    }

    public function test_typical_shows_each_order_number_in_order(): void
    {
        $orders = $this->orders(5);

        $this->blade('<x-recent-orders :orders="$orders" />', ['orders' => $orders])
            ->assertSeeInOrder($orders->pluck('number')->all());
    }

    public function test_overflow_keeps_a_long_customer_name_in_its_title(): void
    {
        $name = 'Maximiliana Featherstonehaugh-Wolfeschlegel';

        $this->blade('<x-recent-orders :orders="$orders" />', ['orders' => $this->orders(1, $name)])
            ->assertSee('title="'.$name.'"', false);
    }

    public function test_error_shows_the_message_with_a_way_to_retry(): void
    {
        $this->blade('<x-recent-orders :orders="$orders" :error="$error" />', [
            'orders' => collect(),
            'error' => "We couldn't load recent orders.",
        ])
            ->assertSee("We couldn't load recent orders.")
            ->assertSee('Try again')
            ->assertDontSee('No orders yet.');
    }

    public function test_loading_announces_that_orders_are_loading(): void
    {
        $this->blade('<x-recent-orders :orders="$orders" loading />', ['orders' => collect()])
            ->assertSee('role="status"', false)
            ->assertDontSee('No orders yet.');
    }
}
