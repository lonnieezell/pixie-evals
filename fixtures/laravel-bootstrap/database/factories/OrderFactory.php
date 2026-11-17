<?php

namespace Database\Factories;

use App\Models\Order;
use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

/**
 * @extends Factory<Order>
 */
class OrderFactory extends Factory
{
    /**
     * @return array<string, mixed>
     */
    public function definition(): array
    {
        return [
            'user_id' => User::factory(),
            'number' => '#'.fake()->unique()->numberBetween(1001, 9999),
            'total' => fake()->randomFloat(2, 10, 500),
            'status' => fake()->randomElement(['paid', 'pending', 'refunded']),
        ];
    }
}
