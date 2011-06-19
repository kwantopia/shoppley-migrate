//
//  LoginViewController.m
//  shoppleyClient
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "LoginViewController.h"

#import "SLDataController.h"

@implementation LoginViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.tableViewStyle = UITableViewStyleGrouped;
        self.autoresizesForKeyboard = YES;
        self.variableHeightRows = YES;
    }
    return self;
}

- (void)dealloc {
    TT_RELEASE_SAFELY(_loginDataSource);
    TT_RELEASE_SAFELY(_isLoadingDataSource);
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    [self.navigationController setNavigationBarHidden:YES animated:NO];
    self.tableView.scrollEnabled = NO;
    self.tableView.backgroundColor = RGBCOLOR(230,230,230);
    
    _emailField = [[[UITextField alloc] init] autorelease];
    _emailField.delegate = self;
    _emailField.placeholder = @"Email";
    _emailField.font = TTSTYLEVAR(font);
    _emailField.keyboardType = UIKeyboardTypeEmailAddress;
    _emailField.autocorrectionType = UITextAutocorrectionTypeNo;
    _emailField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _emailField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _emailField.returnKeyType = UIReturnKeyNext;
    
    _passwordField = [[[UITextField alloc] init] autorelease];
    _passwordField.delegate = self;
    _passwordField.placeholder = @"Password";
    _passwordField.font = TTSTYLEVAR(font);
    _passwordField.secureTextEntry = YES;
    _passwordField.autocorrectionType = UITextAutocorrectionTypeNo;
    _passwordField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _passwordField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _passwordField.returnKeyType = UIReturnKeyGo;
    
    _loginDataSource = [TTListDataSource dataSourceWithObjects:_emailField, _passwordField, nil];
    [_loginDataSource retain];
    self.dataSource = _loginDataSource;
    
    [_emailField becomeFirstResponder];
    
    // Retrieve saved email / password
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    NSString *saved_email = [defaults stringForKey:@"email"];
    NSString *saved_password = [defaults stringForKey:@"password"];
    if (TTIsStringWithAnyText(saved_email)) {
        _emailField.text = saved_email;
    }
    if (TTIsStringWithAnyText(saved_password)) {
        _passwordField.text = saved_password;
    }
    if (TTIsStringWithAnyText(saved_email) && TTIsStringWithAnyText(saved_password)) {
        [self authenticate];
    }
}

#pragma mark Login

- (void)authenticate {
    if (!(TTIsStringWithAnyText(_emailField.text) && TTIsStringWithAnyText(_passwordField.text))) {
        UIAlertView *alert = [[UIAlertView alloc]
                              initWithTitle:@"Login Failure"
                              message:@"Email/password cannot be blank."
                              delegate:self
                              cancelButtonTitle:@"OK"
                              otherButtonTitles: nil];
        [alert show];
        [alert release];
        return;
    }
    
    if (!_isLoadingDataSource) {
        _isLoadingDataSource = [[TTListDataSource dataSourceWithObjects:
                                 [TTTableActivityItem itemWithText:@"Processing..."],
                                 nil]
                                retain];
    }
    self.dataSource = _isLoadingDataSource;

    _emailField.enabled = NO;
    _passwordField.enabled = NO;
    
    if ([[SLDataController sharedInstance] authenticateEmail:_emailField.text password:_passwordField.text]) {
        [[TTNavigator navigator] removeAllViewControllers];
        [[TTNavigator navigator] openURLAction:[[TTURLAction actionWithURLPath:@"shoppley://tabbar"] applyAnimated:NO]];
    } else {
        UIAlertView *alert = [[UIAlertView alloc]
                              initWithTitle:@"Login Failure"
                              message:[SLDataController sharedInstance].errorString
                              delegate:self
                              cancelButtonTitle:@"OK"
                              otherButtonTitles: nil];
        [alert show];
        [alert release];
        
        self.dataSource = _loginDataSource;
        _emailField.enabled = YES;
        _passwordField.enabled = YES;
        [_passwordField becomeFirstResponder];
    }
} 

- (BOOL)textFieldShouldReturn:(UITextField *)theTextField {    
    if (_passwordField.text == nil) {
        [_passwordField becomeFirstResponder];
    } else {
        [self authenticate];
    }
    return YES;
}

@end
