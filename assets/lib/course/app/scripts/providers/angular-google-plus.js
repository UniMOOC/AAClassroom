/*! angular-google-plus - v0.1.1 2014-04-27 */
/**
 * Options object available for module
 * options/services definition.
 * @type {Object}
 */
var options = {};

/**
 * googleplus module
 */
angular.module("googleplus", []).provider("GooglePlus", [ function() {
    /**
     * clientId
     * @type {Number}
     */
    options.clientId = null;
    this.setClientId = function(a) {
        options.clientId = a;
        return this;
    };
    this.getClientId = function() {
        return options.clientId;
    };
    /**
     * apiKey
     * @type {String}
     */
    options.apiKey = null;
    this.setApiKey = function(a) {
        options.apiKey = a;
        return this;
    };
    this.getApiKey = function() {
        return options.apiKey;
    };
    /**
     * responseType
     * @type {String}
     */
    options.responseType = 'code token id_token gsession';
    this.setresponseType = function(a) {
        options.responseType = a;
        return this;
    };
    this.getresponseType = function() {
        return options.responseType;
    };
    /**
     * Scopes
     * @default 'https://www.googleapis.com/auth/plus.login'
     * @type {Boolean}
     */
    options.scopes = "https://www.googleapis.com/auth/plus.login";
    this.setScopes = function(a) {
        options.scopes = a;
        return this;
    };
    this.getScopes = function() {
        return options.scopes;
    };
    /**
     * Init Google Plus API
     */
    this.init = function(a) {
        angular.extend(options, a);
    };
    /**
     * This defines the Google Plus Service on run.
     */
    this.$get = [ "$q", "$rootScope", "$timeout", function(a, b, c) {
        /**
       * Create a deferred instance to implement asynchronous calls
       * @type {Object}
       */
        var d = a.defer();
        /**
       * NgGooglePlus Class
       * @type {Class}
       */
        var e = function() {};
        e.prototype.login = function() { 
            d = a.defer();
            gapi.auth.authorize({
                client_id: options.clientId,
                scope: options.scopes,
                immediate: false,
                response_type: options.responseType,
                cookie_policy: 'single_host_origin'
            }, this.handleAuthResult);
            return d.promise;
        };
        e.prototype.checkAuth = function() { 
            d = a.defer();
            
            gapi.auth.authorize({
                client_id: options.clientId,
                scope: options.scopes,
                immediate: true,
                response_type: options.responseType,
                cookie_policy: 'single_host_origin'
            }, this.handleAuthResult);
            
            return d.promise;
        };
        e.prototype.handleClientLoad = function() { 
            gapi.client.setApiKey(options.apiKey);
            gapi.auth.init(function() {});
            c(this.checkAuth, 1);
            return d.promise;
        };
        e.prototype.handleAuthResult = function(a) { 
            if (a && !a.error) {
                d.resolve(a);
                b.$apply();
            } else {
                d.reject(a);
            }
        };
        e.prototype.getUser = function() {
            var c = a.defer();
            gapi.client.load('oauth2', 'v2', function() {
                gapi.client.oauth2.userinfo.get().execute(function(a) {
                    c.resolve(a);
                    b.$apply();
                });
            });
            return c.promise;
        };
        
        // Devuelvo usuario formateado al gusto
        e.prototype.loadProfile = function() { 
            var f = a.defer();
            this.getUser().then(function(u){ 
                var user = { 
                    "name": u.name,
                    "email": u.email,
                    "link_profile": u.link,
                    "img_url": u.picture
                }
                f.resolve(user);
            });
            return f.promise;
        };
        
        e.prototype.getToken = function() {
            return gapi.auth.getToken();
        };
        e.prototype.setToken = function(a) {
            return gapi.auth.setToken(a);
        };
        return new e();
    } ];
} ]).run([ function(GooglePlus) {
    var a = document.createElement("script");
    a.type = "text/javascript";
    a.async = true;
    a.src = "https://apis.google.com/js/client:platform.js?onload=Callback";
    var b = document.getElementsByTagName("script")[0];
    b.parentNode.insertBefore(a, b);
} ]);

function Callback(){ 
    angular.element('body').scope().LoadGooglePlus()
}




