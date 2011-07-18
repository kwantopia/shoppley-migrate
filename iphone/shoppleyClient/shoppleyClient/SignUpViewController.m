//
//  SignUpViewController.m
//  shoppleyClient
//
//  Created by yod on 7/17/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SignUpViewController.h"

#import "SLDataController.h"

@implementation SignUpViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.tableViewStyle = UITableViewStyleGrouped;
        self.autoresizesForKeyboard = YES;
        self.variableHeightRows = YES;
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_signupDataSource);
    TT_RELEASE_SAFELY(_emailField);
    TT_RELEASE_SAFELY(_passwordField);
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    self.title = @"Sign Up";
    
    self.tableView.scrollEnabled = YES;
    self.tableView.backgroundColor = RGBCOLOR(230,230,230);
    
    _emailField = [[UITextField alloc] init];
    _emailField.delegate = self;
    _emailField.placeholder = @"Email Address";
    _emailField.font = TTSTYLEVAR(font);
    _emailField.keyboardType = UIKeyboardTypeEmailAddress;
    _emailField.autocorrectionType = UITextAutocorrectionTypeNo;
    _emailField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _emailField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _emailField.returnKeyType = UIReturnKeyNext;
    
    _phoneField = [[UITextField alloc] init];
    _phoneField.delegate = self;
    _phoneField.placeholder = @"Phone Number";
    _phoneField.font = TTSTYLEVAR(font);
    _phoneField.keyboardType = UIKeyboardTypeNumberPad;
    _phoneField.autocorrectionType = UITextAutocorrectionTypeNo;
    _phoneField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _phoneField.returnKeyType = UIReturnKeyNext;
    
    _zipcodeField = [[UITextField alloc] init];
    _zipcodeField.delegate = self;
    _zipcodeField.placeholder = @"Zip Code";
    _zipcodeField.font = TTSTYLEVAR(font);
    _zipcodeField.keyboardType = UIKeyboardTypeNumberPad;
    _zipcodeField.autocorrectionType = UITextAutocorrectionTypeNo;
    _zipcodeField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _zipcodeField.returnKeyType = UIReturnKeyNext;
    
    _passwordField = [[UITextField alloc] init];
    _passwordField.delegate = self;
    _passwordField.placeholder = @"Password";
    _passwordField.font = TTSTYLEVAR(font);
    _passwordField.secureTextEntry = YES;
    _passwordField.autocorrectionType = UITextAutocorrectionTypeNo;
    _passwordField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _passwordField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _passwordField.returnKeyType = UIReturnKeyNext;
    
    _passwordField1 = [[UITextField alloc] init];
    _passwordField1.delegate = self;
    _passwordField1.placeholder = @"Verify Password";
    _passwordField1.font = TTSTYLEVAR(font);
    _passwordField1.secureTextEntry = YES;
    _passwordField1.autocorrectionType = UITextAutocorrectionTypeNo;
    _passwordField1.clearButtonMode = UITextFieldViewModeWhileEditing;
    _passwordField1.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _passwordField1.returnKeyType = UIReturnKeyGo;
    
    TTTableButton* signupButton = [TTTableButton itemWithText:@"Sign Up" delegate:self selector:@selector(signup)];
    
    _signupDataSource = [[TTListDataSource dataSourceWithObjects:_emailField, _phoneField, _zipcodeField, _passwordField, _passwordField1, signupButton, nil] retain];
    self.dataSource = _signupDataSource;
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.navigationController setNavigationBarHidden:NO animated:YES];
}

#pragma mark Sign Up

- (void)signup {
    NSString* error = @"";
    if (!(TTIsStringWithAnyText(_emailField.text))) {
        error = @"Email Address cannot be blank.";
        [_emailField becomeFirstResponder];
    } else if (!(TTIsStringWithAnyText(_phoneField.text))) {
        error = @"Phone Number cannot be blank.";
        [_phoneField becomeFirstResponder];
    } else if (!(TTIsStringWithAnyText(_zipcodeField.text))) {
        error = @"Zip Code cannot be blank.";
        [_zipcodeField becomeFirstResponder];
    } else if (!(TTIsStringWithAnyText(_passwordField.text))) {
        error = @"Password cannot be blank.";
        [_passwordField becomeFirstResponder];
    } else if (![_passwordField.text isEqualToString:_passwordField1.text]) {
        error = @"Passwords mismatch. Please type them again.";
        _passwordField.text = @"";
        _passwordField1.text = @"";
        [_passwordField becomeFirstResponder];
    }
    
    if (TTIsStringWithAnyText(error)) {
        UIAlertView *alert = [[UIAlertView alloc]
                              initWithTitle:@""
                              message:error
                              delegate:self
                              cancelButtonTitle:@"OK"
                              otherButtonTitles: nil];
        [alert show];
        [alert release];
        return;
    }
    
    self.dataSource = [TTListDataSource dataSourceWithObjects:[TTTableActivityItem itemWithText:@"Processing..."], nil];
    
    if ([[SLDataController sharedInstance] registerEmail:_emailField.text password:_passwordField.text phone:_phoneField.text zipcode:_zipcodeField.text]) {
        [[TTNavigator navigator] removeAllViewControllers];
        [[TTNavigator navigator] openURLAction:[[TTURLAction actionWithURLPath:@"shoppley://tabbar"] applyAnimated:NO]];
    } else {
        UIAlertView *alert = [[UIAlertView alloc]
                              initWithTitle:@""
                              message:[SLDataController sharedInstance].errorString
                              delegate:self
                              cancelButtonTitle:@"OK"
                              otherButtonTitles: nil];
        [alert show];
        [alert release];
        
        self.dataSource = _signupDataSource;
    }
} 

- (BOOL)textFieldShouldReturn:(UITextField *)textField {
    if (textField == _emailField) {
        [_phoneField becomeFirstResponder];
    } else if (textField == _phoneField) {
        [_zipcodeField becomeFirstResponder];
    } else if (textField == _zipcodeField) {
        [_passwordField becomeFirstResponder];
    } else if (textField == _passwordField) {
        [_passwordField1 becomeFirstResponder];
    } else if (textField == _passwordField1) {
        [self signup];
    }
    return YES;
}

@end
