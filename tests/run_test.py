#!/usr/bin/env python3
from test_version import TestVersion
from test_utils import TestScreenshot, TestRun, TestDelay, TestA11Y, TestLock, TestI18N
from dogtail.logging import info_message
import dogtail

#
#info_message(message="====================================")
#info_message(message="Executiong tests for dogtail.version")
#info_message(message="====================================")
#run_test0 = TestVersion()
#
#info_message(message="TestVersion.test_version_from_string_list()")
#run_test0.test_version_from_string_list()
#info_message(message="TestVersion.test_version_from_string()")
#run_test0.test_version_from_string()
#info_message(message="TestVersion.test_version_from_string_dedicated()")
#run_test0.test_version_from_string_dedicated()
#info_message(message="TestVersion.test_version_less_than()")
#run_test0.test_version_less_than()
#info_message(message="TestVersion.test_version_more_than()")
#run_test0.test_version_more_than()
#info_message(message="TestVersion.test_version_equals()")
#run_test0.test_version_equals()
#
#
#info_message(message="====================================")
#info_message(message="Executiong tests for dogtail.utils")
#info_message(message="====================================")
##run_test1_0 = TestScreenshot()
##run_test1_0.make_expected_and_compare("/tmp/dogtail-test-screenshot.jpg")
##run_test1_0.test_screenshot_incorrect_timestamp()
##run_test1_0.test_screenshot_default()
##run_test1_0.test_screenshot_basename()
##run_test1_0.test_screenshot_no_time_stamp()
##run_test1_0.test_screenshot_jpeg()
##run_test1_0.test_screenshot_unknown_format()
##run_test1_0.test_screenshot_incorrect_timestamp()
##run_test1_0.test_screenshot_incorrect_timestamp()
##run_test1_0.test_screenshot_incorrect_timestamp()
#
#info_message(message="TestRun()")
#run_test1_1 = TestRun()
#info_message(message="TestRun().setUp")
#run_test1_1.setUp()
#info_message(message="TestRun().tearDown")
#run_test1_1.tearDown()
#info_message(message="TestRun().test_run")
#run_test1_1.test_run()
#info_message(message="TestRun().test_run_wrong")
#run_test1_1.test_run_wrong()
#info_message(message="TestRun().test_run_dumb")
#run_test1_1.test_run_dumb()
#import os
#os.system("killall gtk3-demo")
#
#info_message(message="TestDelay()")
#run_test1_2 = TestDelay()
#info_message(message="TestDelay().test_doDelay_implicit()")
#run_test1_2.test_doDelay_implicit()
#info_message(message="TestDelay().test_doDelay_explicit()")
#run_test1_2.test_doDelay_explicit()
#info_message(message="TestDelay().test_doDelay_logger()")
#run_test1_2.test_doDelay_logger()
#
#info_message(message="TestA11Y()")
#run_test1_3 = TestA11Y()
#info_message(message="TestA11Y().test_bail_when_a11y_disabled()")
#run_test1_3.test_bail_when_a11y_disabled()
#info_message(message="TestA11Y().test_enable_a11y()")
#run_test1_3.test_enable_a11y()
#
#info_message(message="TestLock()")
#run_test1_4 = TestLock()
#info_message(message="TestLock().tearDown")
#run_test1_4.tearDown()
#info_message(message="TestLock().test_set_unrandomized_lock")
#run_test1_4.test_set_unrandomized_lock()
#info_message(message="TestLock().test_double_lock")
#run_test1_4.test_double_lock()
#dogtail.utils.Lock(lockname='dogtail-test.lock', randomize=False).unlock()
#info_message(message="TestLock().test_double_unlock")
#run_test1_4.test_double_unlock()
#info_message(message="TestLock().test_randomize")
#run_test1_4.test_randomize()
#
#info_message(message="TestI18N()")
#run_test1_5 = TestI18N()
#info_message(message="TestI18N().test_load_all_translations_for_language")
#run_test1_5.test_load_all_translations_for_language()
#
#
#info_message(message="====================================")
#info_message(message="Executiong tests for dogtail.tree")
#info_message(message="====================================")
#from test_tree import TestNode, TestSelection, TestValue, TestSearching, TestUnicodeNames, TestDump
#list_of_tests = ["test_get_bogus","test_get_name","test_set_name","test_get_debugName",
#"test_set_debugName","test_get_roleName","test_set_roleName","test_get_role","test_set_role",
#"test_get_description","test_set_description","test_get_parent","test_set_parent",
#"test_get_children","test_set_children","test_get_children_with_limit","test_get_combo_value",
#"test_get_URI_not_implemented","test_set_text","test_text_set_error","test_caretOffset",
#"test_comboValue","test_getStateSet","test_setStateSet","test_get_relations","test_get_labelee",
#"test_set_labelee","test_get_labeler","test_set_labeller","test_get_sensitive","test_set_sensitive",
#"test_get_showing","test_set_showing","test_get_visible","test_set_visible","test_get_actions",
#"test_set_actions","test_get_extents","test_get_extens_wrong","test_set_extents","test_get_position",
#"test_get_position_not_implemented","test_set_position","test_get_size_not_implemented",
#"test_set_size","test_get_toolkit","test_set_toolkit","test_get_ID","test_set_ID","test_checked",
#"test_dead","test_contains","test_childAtPoint","test_click","test_doubleClick","test_point",
#"test_typeText_nonfucable"]
#info_message(message="TestNode()")
#for test in list_of_tests:
#    info_message(message="TestNode().%s" % test)
#    testing = TestNode()
#    testing.setUp()
#    getattr(testing, test)()
#    testing.tearDown()
#
#
#list_of_tests = ["test_tabs", "test_iconView"]
#info_message(message="TestSelection()")
#for test in list_of_tests:
#    info_message(message="TestSelection().%s" % test)
#    testing = TestSelection()
#    testing.setUp()
#    getattr(testing, test)()
#    testing.tearDown()
#
#list_of_tests = ["test_get_value", "test_set_value", "test_min_value", "test_max_value", "test_min_value_increment"]
#info_message(message="TestValue()")
#for test in list_of_tests:
#    info_message(message="TestValue().%s" % test)
#    testing = TestValue()
#    testing.setUp()
#    getattr(testing, test)()
#    testing.tearDown()
#
#
#list_of_tests = ["test_findChildren", "test_findChild_lambda", "test_findChildren2", 
#"test_findChildren2_lambda", "test_findChildren_lambdas", "test_findAncestor", "test_isChild", 
#"test_getUserVisibleStrings", "test_satisfies", "test_absoluteSearchPath", 
#"test_compare_equal_search_paths", "test_compare_unequal_search_paths_different_length", 
#"test_compare_unequal_search_paths_same_length", "test_get_search_path_length", 
#"test_iterate_search_path", "test_make_script_method_call_from_search_path", 
#"test_get_relative_search_path_for_path", "test_get_prefix_for_search_path", "test_get_predicate", 
#"test_getRelativeSearch_app", "test_getRelativeSearch_widget", "test_findChildren_non_recursive", 
#"test_find_by_shortcut", "test_find_by_shortcut2"]
#info_message(message="TestSearching()")
#for test in list_of_tests:
#    info_message(message="TestSearching().%s" % test)
#    testing = TestSearching()
#    testing.setUp()
#    getattr(testing, test)()
#    testing.tearDown()
#
#
#list_of_tests = ["setUp", "test_unicode_char_in_name", "test_unicode_char_in_name_click", 
#"test_unicode_logging_nocrash", "tearDown"]
#info_message(message="TestUnicodeNames()")
#for test in list_of_tests:
#    info_message(message="TestUnicodeNames().%s" % test)
#    testing = TestUnicodeNames()
#    testing.setUp()
#    getattr(testing, test)()
#    testing.tearDown()
#
#
#list_of_tests = ["test_dump_to_stdout", "test_dump_with_actions"]
#info_message(message="TestDump()")
#for test in list_of_tests:
#    info_message(message="TestDump().%s" % test)
#    testing = TestDump()
#    testing.setUp()
#    getattr(testing, test)()
#    testing.tearDown()


info_message(message="====================================")
info_message(message="Executiong tests for dogtail.rawinput")
info_message(message="====================================")
from test_rawinput import TestRawinput
list_of_tests = ["test_motion", "test_motion_with_trajectory",
"test_check_coordinates_direct", "test_check_coordinates_builtin",
"test_doubleClick", "test_click", "test_press_release", "test_drag",
"test_drag_with_trajectory", "test_pressKey_no_such_key", "test_keyCombo_simple",
"test_keyCombo_multi", "test_keyCombo_wrong_key", "test_typeText"]
info_message(message="TestRawinput()")
for test in list_of_tests:
    info_message(message="TestRawinput().%s" % test)
    testing = TestRawinput()
    testing.setUp()
    getattr(testing, test)()
    testing.tearDown()
