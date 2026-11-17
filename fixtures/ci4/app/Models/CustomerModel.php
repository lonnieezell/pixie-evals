<?php

namespace App\Models;

use CodeIgniter\Model;
use Faker\Generator;

class CustomerModel extends Model
{
    protected $table         = 'customers';
    protected $returnType    = 'array';
    protected $allowedFields = ['name', 'email'];
    protected $useTimestamps = true;

    /**
     * Fake data for Fabricator: seeds and previews.
     */
    public function fake(Generator &$faker): array
    {
        return [
            'name'  => $faker->name(),
            'email' => $faker->unique()->safeEmail(),
        ];
    }
}
