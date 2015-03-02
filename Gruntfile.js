// Generated on 2014-10-11 using generator-angular 0.9.8
'use strict';

// # Globbing
// for performance reasons we're only matching one level down:
// 'test/spec/{,*/}*.js'
// use this if you want to recursively match all subfolders:
// 'test/spec/**/*.js'

module.exports = function (grunt) {

  // Load grunt tasks automatically
  require('load-grunt-tasks')(grunt);

  // Time how long tasks take. Can help when optimizing build times
  require('time-grunt')(grunt);

  // Configurable paths for the application
  var appConfig = {
    app: 'assets/lib/course/app',
    adminApp : 'assets/lib/admin/app',
    dist: 'assets/lib/course/dist',
    adminDist: 'assets/lib/admin/dist',
    root: 'assets/lib/course',
    adminRoot: 'assets/lib/admin',

    rootView: 'modules/um_course/views/course.html',
    rootViewBase: 'modules/um_course/views',
    rootViewFile: 'course.html',

    adminView: 'modules/um_course/views/admin.html',
    adminViewBase: 'modules/um_course/views',
    adminViewFile: 'admin.html',

    gcbBuildPath: 'build',
    gcbMainViewPath: 'build/modules/um_course/views'
  };

  // Define the configuration for all the tasks
  grunt.initConfig({

    // Project settings
    yeoman: appConfig,

      less: {
          development: {

              options: {
              		cleancss: false,
                    compress: false
					//yuicompress: false,
					//optimization: 2
                },
                files: [
                    {
                        expand: true,
                        cwd: '<%= yeoman.app %>/styles/',
                        src: 'main.less',
                        dest: '<%= yeoman.app %>/styles/',
                        ext: '.css'
                    }
                ]
          }
      },

      i18nextract: {
		  todo: {
			prefix:   '',
			suffix:   '.json',
			src:      [ '<%= yeoman.rootView %>', '<%= yeoman.app %>/views/{,*/}*.html', '<%= yeoman.app %>/scripts/{,*/}*.js' ],
			lang:     ['es', 'en'],
			dest:     '<%= yeoman.app %>/i18n/'
		  }

	  },

    // Watches files for changes and runs tasks based on the changed files
    watch: {
      bower: {
        files: ['<%= yeoman.root %>/bower.json'],
        tasks: ['wiredep']
      },
      js: {
        files: ['<%= yeoman.app %>/scripts/{,*/}*.js'],
        tasks: ['newer:jshint:all'],
        options: {
          livereload: '<%= connect.options.livereload %>'
        }
      },
      jsTest: {
        files: ['<%= yeoman.root %>/test/spec/{,*/}*.js'],
        tasks: ['newer:jshint:test', 'karma']
      },
      less: {
            files: ['<%= yeoman.app %>/styles/{,*/}*.less'],
            tasks: ['less']
      },
      styles: {
        files: ['<%= yeoman.app %>/styles/{,*/}*.css'],
        tasks: ['newer:copy:styles', 'autoprefixer']
      },
      gruntfile: {
        files: ['Gruntfile.js']
      },
      livereload: {
        options: {
          livereload: '<%= connect.options.livereload %>'
        },
        files: [
          '<%= yeoman.rootViewBase %>/{,*/}*.html',
          '<%= yeoman.app %>/{,*/}*.html',
          '<%= yeoman.app %>/{,*/}/{,*/}*.html',
          '.tmp/styles/{,*/}*.css',
          '<%= yeoman.app %>/images/{,*/}*.{png,jpg,jpeg,gif,webp,svg}'
        ]
      }
    },

    // The actual grunt server settings
    connect: {
      options: {
        port: 9000,
        // Change this to '0.0.0.0' to access the server from outside.
        hostname: 'localhost',
        livereload: 35729
      },
      livereload: {
        options: {
          open: true,
          middleware: function (connect) {
            return [
              connect.static('.tmp'),
              connect().use(
                '<%= yeoman.root %>/bower_components',
                connect.static('<%= yeoman.root %>/bower_components')
              ),
              connect.static(appConfig.app),
              connect.static(appConfig.rootViewBase)
            ];
          }
        }
      },
      test: {
        options: {
          port: 9001,
          middleware: function (connect) {
            return [
              connect.static('.tmp'),
              connect.static('<%= yeoman.root %>/test'),
              connect().use(
                '<%= yeoman.root %>/bower_components',
                connect.static('./bower_components')
              ),
              connect.static(appConfig.app)
            ];
          }
        }
      },
      dist: {
        options: {
          open: true,
          base: '<%= yeoman.dist %>'
        }
      }
    },

    // Make sure code styles are up to par and there are no obvious mistakes
    jshint: {
      options: {
        jshintrc: '.jshintrc',
        reporter: require('jshint-stylish'),
        devel:true
      },
      all: {
        src: [
          'Gruntfile.js',
          '<%= yeoman.app %>/scripts/{,*/}*.js'
        ]
      },
      test: {
        options: {
          jshintrc: 'test/.jshintrc'
        },
        src: ['test/spec/{,*/}*.js']
      }
    },

    // Empties folders to start fresh
    clean: {
      dist: {
        files: [{
          dot: true,
          src: [
            '.tmp',
            '<%= yeoman.dist %>/{,*/}*',
            '!<%= yeoman.dist %>/.git*'
          ]
        }]
      },
      gcbBuildBefore: {
         src: 'build'
      },
      gcbBuildAfter: {
         files: [{
          dot: true,
          src: [
            '<%= yeoman.gcbBuildPath %>/assets/lib/*/*',
            '!<%= yeoman.gcbBuildPath %>/assets/lib/**/dist'
          ]
        }, {
          dot: true,
          src: [
            '<%= yeoman.gcbBuildPath %>/assets/lib/*/dist/course.html'
          ]
        }]
      },
      server: '.tmp'
    },

    // Add vendor prefixed styles
    autoprefixer: {
      options: {
        browsers: ['last 1 version']
      },
      dist: {
        files: [{
          expand: true,
          cwd: '.tmp/styles/',
          src: '{,*/}*.css',
          dest: '.tmp/styles/'
        }]
      }
    },

    // Automatically inject Bower components into the app
    wiredep: {
      app: {
        src: ['<%= yeoman.rootView %>'],
        options: {
            directory: appConfig.root + '/bower_components',
            bowerJson: require('./' + appConfig.root + '/bower.json'),
            ignorePath: '../../../'
        }
      },

      appAdmin: {
        src: ['<%= yeoman.adminView %>'],
        options: {
            directory: './assets/lib/admin/bower_components',
            bowerJson: require('./assets/lib/admin/bower.json'),
            ignorePath: '../../../'
        }
      }
    },

    // Reads HTML for usemin blocks to enable smart builds that automatically
    // concat, minify and revision files. Creates configurations in memory so
    // additional tasks can operate on them
    useminPrepare: {
      html: ['<%= yeoman.rootView %>', '<%= yeoman.adminView %>'],
      options: {
        dest: './',
        root: './',
        flow: {
          html: {
            steps: {
              js: ['concat', 'uglifyjs'],
              css: ['cssmin']
            },
            post: {}
          }
        }
      }
    },

    // Performs rewrites based on filerev and the useminPrepare configuration
    usemin: {
      html: ['<%= yeoman.dist %>/{,*/}*.html'],
      css: ['<%= yeoman.dist %>/styles/{,*/}*.css'],
      options: {
        assetsDirs: ['<%= yeoman.dist %>','<%= yeoman.dist %>/images']
      }
    },

    imagemin: {
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.app %>/images',
          src: '{,*/}*.{png,jpg,jpeg,gif}',
          dest: '<%= yeoman.dist %>/images'
        }]
      }
    },

    svgmin: {
      dist: {
        files: [{
          expand: true,
          cwd: '<%= yeoman.app %>/images',
          src: '{,*/}*.svg',
          dest: '<%= yeoman.dist %>/images'
        }]
      }
    },

    htmlmin: {
      dist: {
        options: {
          collapseWhitespace: true,
          conservativeCollapse: true,
          collapseBooleanAttributes: true,
          removeCommentsFromCDATA: true,
          removeOptionalTags: true
        },
        files: [{
          expand: true,
          cwd: '<%= yeoman.dist %>',
          src: ['*.html', 'views/{,*/}*.html'],
          dest: '<%= yeoman.dist %>'
        }]
      }
    },

    // ng-annotate tries to make the code safe for minification automatically
    // by using the Angular long form for dependency injection.
    ngAnnotate: {
      dist: {
        files: [{
          expand: true,
          cwd: '.tmp/concat/scripts',
          src: ['*.js', '!oldieshim.js'],
          dest: '.tmp/concat/scripts'
        }]
      }
    },

    // Replace Google CDN references
    cdnify: {
      dist: {
        html: ['<%= yeoman.dist %>/*.html']
      }
    },

    // Copies remaining files to places other tasks can use
    copy: {
      dist: {
        files: [{
          expand: true,
          dot: true,
          cwd: '<%= yeoman.app %>',
          dest: '<%= yeoman.dist %>',
          src: [
            '*.{ico,png,txt}',
            '.htaccess',
            '*.html',
            'views/{,*/}*.html',
            'images/{,*/}*.{png,jpg,jpeg,gif}',
            'fonts/*',
            'fake-API/*'
          ]
        }, {
          expand: true,
          dot: true,
          cwd: 'assets/lib/admin/app',
          dest: 'assets/lib/admin/dist',
          src: [
            '*.{ico,png,txt}',
            '.htaccess',
            '*.html',
            'views/{,*/}*.html',
            'images/{,*/}*.{png,jpg,jpeg,gif}',
            'fonts/*',
            'fake-API/*'
          ]
        }, {
          expand: true,
          cwd: '<%= yeoman.rootViewBase %>',
          dest: '<%= yeoman.dist %>',
          src: ['<%= yeoman.rootViewFile %>']
        }, {
          expand: true,
          cwd: '<%= yeoman.adminViewBase %>',
          dest: '<%= yeoman.dist %>',
          src: ['<%= yeoman.adminViewFile %>']
        }, {
          expand: true,
          cwd: '.tmp/images',
          dest: '<%= yeoman.dist %>/images',
          src: ['generated/*']
        }, {
          expand: true,
          cwd: './<%= yeoman.root %>/bower_components/fontawesome/fonts',
          src: '*',
          dest: '<%= yeoman.dist %>/fonts'
        }, {
          expand: true,
          cwd: '<%= yeoman.root %>/bower_components/bootstrap/dist',
          src: 'fonts/*',
          dest: '<%= yeoman.dist %>'
        }, {
          expand: true,
          cwd: './<%= yeoman.root %>/bower_components/fontawesome/fonts',
          src: '*',
          dest: '<%= yeoman.adminDist %>/fonts'
        }, {
          expand: true,
          cwd: '<%= yeoman.root %>/bower_components/bootstrap/dist',
          src: 'fonts/*',
          dest: '<%= yeoman.adminDist %>'
        }
        ]
      },
      gcbBuild: { // Copia todo, excepto bower y npm, .ai, .psd y .tmp
          files: [
              { // Añadir course a
                  expand: true,
                  cwd: '.',
                  dest: 'build',
                  src: ['**', '!**/*.ai', '!**/*.psd', '!**/.tmp/**', '!**/*.pyc', '!**/bower_components/**', '!**/node_modules/**']
              },
              {
                  expand: true,
                  cwd: '<%= yeoman.dist %>',
                  src: '<%= yeoman.rootViewFile %>',
                  dest: '<%= yeoman.gcbMainViewPath %>'
              },
              {
                  expand: true,
                  cwd: '<%= yeoman.dist %>',
                  src: '<%= yeoman.adminViewFile %>',
                  dest: '<%= yeoman.gcbMainViewPath %>'
              }
          ]
      },
      styles: {
        expand: true,
        cwd: '<%= yeoman.app %>/styles',
        dest: '.tmp/styles/',
        src: '{,*/}*.css'
      }
    },

    // Run some tasks in parallel to speed up the build process
    concurrent: {
      server: [
        'copy:styles'
      ],
      test: [
        'copy:styles'
      ],
      dist: [
        'copy:styles',
        'imagemin',
        'svgmin'
      ]
    },

    replace: {
        gcbBuildConstants: {
            src: appConfig.gcbBuildPath + '/assets/lib/course/**/scripts*.js',
            overwrite: true,
            replacements: [{
                from: 'assets/lib/course/app',
                to: 'assets/lib/course/dist'
            }]
        },
        gcbBuildConstantsAdmin: {
            src: appConfig.gcbBuildPath + '/assets/lib/admin/**/scripts*.js',
            overwrite: true,
            replacements: [{
                from: 'assets/lib/admin/app',
                to: 'assets/lib/admin/dist'
            }]
        }
    },

    gae: {
        options: {
            path: 'build'
        },
        run: {
            action: 'run'
        },
        deploy: {
            action: 'update'
        }
    },
  });

	grunt.loadNpmTasks('grunt-angular-translate');

  grunt.registerTask('gcbBuild', [
    'clean:gcbBuildBefore',
    'copy:gcbBuild',
    'clean:gcbBuildAfter',
    'replace'
  ]);

  grunt.registerTask('deploy', [
    'gae:deploy'
  ]);

  grunt.registerTask('build', [
    'clean:dist',
    'wiredep',
    'useminPrepare',
    'less',
    'autoprefixer',
    'concat',
    'ngAnnotate',
    'copy:dist',
    'cssmin',
    'uglify',
    'usemin',
    'htmlmin'
  ]);

  grunt.registerTask('translate', [
    'i18nextract'
  ]);

  grunt.registerTask('buildComplete', [
    'build',
    'gcbBuild'
  ]);

  grunt.registerTask('buildCompleteDeploy', [
    'build',
    'gcbBuild',
    'deploy',
    'clean:gcbBuildBefore'
  ]);

  grunt.registerTask('default', [
    'build'
  ]);
};
