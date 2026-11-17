<?php

namespace App\Database\Migrations;

use CodeIgniter\Database\Migration;

class CreateShopTables extends Migration
{
    public function up(): void
    {
        $this->forge->addField([
            'id'         => ['type' => 'INTEGER', 'auto_increment' => true],
            'name'       => ['type' => 'VARCHAR', 'constraint' => 255],
            'email'      => ['type' => 'VARCHAR', 'constraint' => 255],
            'created_at' => ['type' => 'DATETIME', 'null' => true],
            'updated_at' => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addPrimaryKey('id');
        $this->forge->createTable('customers');

        $this->forge->addField([
            'id'          => ['type' => 'INTEGER', 'auto_increment' => true],
            'customer_id' => ['type' => 'INTEGER'],
            'number'      => ['type' => 'VARCHAR', 'constraint' => 20],
            'total'       => ['type' => 'DECIMAL', 'constraint' => '8,2'],
            'status'      => ['type' => 'VARCHAR', 'constraint' => 20],
            'created_at'  => ['type' => 'DATETIME', 'null' => true],
            'updated_at'  => ['type' => 'DATETIME', 'null' => true],
        ]);
        $this->forge->addPrimaryKey('id');
        $this->forge->createTable('orders');
    }

    public function down(): void
    {
        $this->forge->dropTable('orders');
        $this->forge->dropTable('customers');
    }
}
