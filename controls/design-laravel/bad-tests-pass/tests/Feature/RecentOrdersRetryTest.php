<?php

namespace Tests\Feature;

use Tests\TestCase;

// Red: the run left this test failing. The component labels its retry link "Try again".
class RecentOrdersRetryTest extends TestCase
{
    public function test_error_offers_a_retry_link(): void
    {
        $this->blade('<x-recent-orders :orders="$orders" :error="$error" />', [
            'orders' => collect(),
            'error' => "We couldn't load recent orders.",
        ])->assertSee('Retry');
    }
}
