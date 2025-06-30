const express = require('express');
const app = express();
const sequelize = require('sequelize');

//declaracion de la base de datos
const db = new sequelize('curso', 'root', '', {
    host: 'localhost',
    dialect: 'mysql'
});

//definimos el modelo de la base de datos (tablas)
const productos = db.define('productos', {
    ref: {
        type: sequelize.INTEGER,
        primaryKey: true,
        autoIncrement: true
    },
    nombre: sequelize.STRING,
    precio: sequelize.DECIMAL(10, 2),
    stock: sequelize.INTEGER,
    id_categoria: {
        type: sequelize.INTEGER,
        allowNull: true,
        references: {
            model: "categorias", //tabla a la que se hace referencia
            key: 'id' //PK de la tabla
        }
    }
}, {
    timestamps: false
})

//definimos el modelo la tabla categorías
////////////////////

//definimos las relaciones de manera externa al modelo
// productos.belongsTo(categorias, {foreignKey: 'id_categoria'})
// categorias.hasMany(productos, {foreignKey: 'id_categoria'});

//nos conectamos a la base de datos
db.authenticate().then(() => {
    console.log('Conexion a la base de datos establecida');
}).catch(err => {
    console.log(err);
});

//mostrar todos los productos
// productos.findAll({ atributes: ['ref', 'nombre', 'precio'] }).then(productos => {
//     const productosJson = JSON.stringify(productos);
//     console.log(productosJson);
// }).catch(err => {
//     console.log(err);
// })

//mostrar un producto definiendo una referencia
// productos.findAll({ atributes: ['ref', 'nombre', 'precio'], where: { nombre: 3 } }).then(productos => {
//     
//     console.log(productos.toJSON());
// }).catch(err => {
//     console.log(err);
// })

// método nativo buscar por PK
productos.findByPk(3).then(productos => {
    console.log(productos.toJSON());
}).catch(err => {
    console.log(err);
})

//creación de un producto
// productos.create({
//     nombre: "silla gamer",
//     precio: 500,
//     stock: 10
// }).then(producto => {
//     console.log("Prducto añadido: " + producto);
// }).catch(err => {
//     console.log(err);
// })

//actualizar un registro
// productos.update(
//     {
//         nombre: "Silla Gamer",
//         precio: 100,
//     }, {
//     where: {
//         ref: 11
//     }
// }
// ).then(producto => {
//     console.log(producto);
// }).catch(err => {
//     console.log(err);
// })

//eliminar un registro
// productos.destroy({
//     where: {
//         ref: 11
//     }
// }).then(producto => {
//     console.log("producto borrado");
// }).catch(err => {
//     console.log(err);
// })




app.listen(4000, () => {
    console.log('Servidor activo en la url http://localhost:4000');
});
