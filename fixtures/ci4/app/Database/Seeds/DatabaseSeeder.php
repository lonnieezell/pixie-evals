<?php

namespace App\Database\Seeds;

use App\Models\CustomerModel;
use App\Models\OrderModel;
use CodeIgniter\Database\Seeder;
use CodeIgniter\Test\Fabricator;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $customers = new Fabricator(CustomerModel::class);
        $customers->getFaker()->seed(1);
        $customers->create(6);

        $orders = new Fabricator(OrderModel::class);
        $orders->getFaker()->seed(2);
        $orders->create(18);
    }
}
