<?php

namespace App\Models;

use CodeIgniter\Model;
use Faker\Generator;

class OrderModel extends Model
{
    protected $table         = 'orders';
    protected $returnType    = 'array';
    protected $allowedFields = ['customer_id', 'number', 'total', 'status'];
    protected $useTimestamps = true;

    /**
     * Fake data for Fabricator: seeds and previews.
     */
    public function fake(Generator &$faker): array
    {
        return [
            'customer_id' => $faker->numberBetween(1, 6),
            'number'      => '#' . $faker->unique()->numberBetween(1001, 9999),
            'total'       => $faker->randomFloat(2, 10, 500),
            'status'      => $faker->randomElement(['paid', 'pending', 'refunded']),
        ];
    }
}
