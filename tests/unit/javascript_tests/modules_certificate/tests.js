describe('certificate criteria user interface', function() {
  window.cb_global = {
    schema: {
      properties: {
        course: {
          properties: {
            certificate_criteria: {
              _inputex : {
                is_peer_assessment_table : {
                  1: true,
                  2: false,
                }
              }
            }
          }
        }
      }
    }
  };

  describe('fill in form', function() {
    beforeEach(function() {
      jasmine.getFixtures().fixturesPath = 'base/';
      loadFixtures(
          'tests/unit/javascript_tests/modules_certificate/fixture.html');
      this.assessmentDropdown = $(".assessment-dropdown select");
    });

    it('selects a peer graded assessment', function() {
      this.assessmentDropdown.val(1);
      onAssignmentDropdownChanged(this.assessmentDropdown);
      expect($(".inputEx-description").is(':visible')).toBe(true);
      expect($(".pass-percent").is(':hidden')).toBe(true);
      expect($(".custom-criteria").is(':hidden')).toBe(true);
    });
    it('selects a machine graded assessment', function() {
      this.assessmentDropdown.val(2);
      onAssignmentDropdownChanged(this.assessmentDropdown);
      expect($(".inputEx-description").is(':hidden')).toBe(true);
      expect($(".pass-percent").is(':visible')).toBe(true);
      expect($(".custom-criteria").is(':hidden')).toBe(true);
    });
    it('selects default', function() {
      this.assessmentDropdown.val("default");
      onAssignmentDropdownChanged(this.assessmentDropdown);
      expect($(".inputEx-description").is(':hidden')).toBe(true);
      expect($(".pass-percent").is(':visible')).toBe(true);
      expect($(".custom-criteria").is(':visible')).toBe(true);
    });
    it('selects custom criterion option', function() {
      this.assessmentDropdown.val("");
      onAssignmentDropdownChanged(this.assessmentDropdown);
      expect($(".inputEx-description").is(':hidden')).toBe(true);
      expect($(".pass-percent").is(':hidden')).toBe(true);
      expect($(".custom-criteria").is(':visible')).toBe(true);
    });
    it('sets a custom criterion directly', function() {
      var custom_dropdown = $(".custom-criteria select");
      custom_dropdown.val("something");
      onCustomCriteriaDropdownChanged(custom_dropdown);
      expect($(".assessment-dropdown").is(':visible')).toBe(true);
      expect($(".inputEx-description").is(':hidden')).toBe(true);
      expect($(".pass-percent").is(':hidden')).toBe(true);
    });
  });

  describe('save form', function() {
    var criteria = [];
    window.cb_global.form = {
      getValue : function() {
        return {
          course: {
            certificate_criteria : criteria
          }
        }
      }
    };
    window.cbShowMsg = function (unusedMessage) {
      return;
    }
    afterEach(function() {
      while(criteria.length > 0) {
        criteria.pop();
      }
    });
    it('submits a machine graded assessment with pass percent', function() {
      criteria.push(
        {assessment_id: 2, pass_percent: "20", custom_criteria: ""}
      );
      expect(onCourseSettingsSave()).toBe(true);
    });
    it('rejects a machine graded assessment without pass percent', function() {
      criteria.push(
        {assessment_id: 2, pass_percent: "", custom_criteria: ""}
      );
      expect(onCourseSettingsSave()).toBe(false);
    });
    it('submits a peer graded assessment without pass percent', function() {
      criteria.push(
        {assessment_id: 1, pass_percent: "", custom_criteria: ""}
      );
      expect(onCourseSettingsSave()).toBe(true);
    });
    it('rejects criterion with no assessment field specified', function() {
      criteria.push(
        {assessment_id: "default", pass_percent: "", custom_criteria: ""}
      );
      expect(onCourseSettingsSave()).toBe(false);
    });
    it('rejects -- Custom criterion -- without specifying an actual custom' +
        'criterion', function() {
      criteria.push(
        {assessment_id: "", pass_percent: "", custom_criteria: ""}
      );
      expect(onCourseSettingsSave()).toBe(false);
    });
    it('submits -- Custom criterion -- with an actual custom criterion' +
      'specified', function() {
      criteria.push(
        {assessment_id: "", pass_percent: "", custom_criteria: "something"}
      );
      expect(onCourseSettingsSave()).toBe(true);
    });
  });
});
