const ContentRegistry = artifacts.require("ContentRegistry");

module.exports = function (deployer) {
  deployer.deploy(ContentRegistry);
};
