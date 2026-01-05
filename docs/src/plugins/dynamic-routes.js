module.exports = function dynamicRoutesPlugin(context, options) {
  return {
    name: "plugin-dynamic-routes",

    async contentLoaded({ content, actions }) {
      const { routes } = options;
      const { addRoute } = actions;

      routes.forEach((route) => {
        addRoute(route);
      });
    },
  };
};
