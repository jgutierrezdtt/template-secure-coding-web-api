// src/routes/graphql.js
// PASO 4: GraphQL — introspection, depth limit e inyeccion en resolvers

const { ApolloServer } = require("@apollo/server");
const depthLimit = require("graphql-depth-limit");

const resolvers = {
  Query: {
    async searchUsers(_, { name }) {
      const result = await db.query(
        "SELECT id, username FROM users WHERE username ILIKE $1",
        [`%${name}%`]
      );
      return result.rows;
    }
  }
};

const server = new ApolloServer({
  typeDefs,
  resolvers,
  introspection: process.env.NODE_ENV === "development",
  validationRules: [depthLimit(5)],
});

module.exports = server;
