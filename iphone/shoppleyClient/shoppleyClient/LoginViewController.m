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
    TT_RELEASE_SAFELY(_emailField);
    TT_RELEASE_SAFELY(_passwordField);
    [super dealloc];
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    [self.navigationController setNavigationBarHidden:YES animated:NO];
    self.tableView.backgroundColor = RGBCOLOR(230,230,230);
    
    _emailField = [[UITextField alloc] init];
    _emailField.delegate = self;
    _emailField.placeholder = @"Email";
    _emailField.font = TTSTYLEVAR(font);
    _emailField.keyboardType = UIKeyboardTypeEmailAddress;
    _emailField.autocorrectionType = UITextAutocorrectionTypeNo;
    _emailField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _emailField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _emailField.returnKeyType = UIReturnKeyNext;
    
    _passwordField = [[UITextField alloc] init];
    _passwordField.delegate = self;
    _passwordField.placeholder = @"Password";
    _passwordField.font = TTSTYLEVAR(font);
    _passwordField.secureTextEntry = YES;
    _passwordField.autocorrectionType = UITextAutocorrectionTypeNo;
    _passwordField.clearButtonMode = UITextFieldViewModeWhileEditing;
    _passwordField.autocapitalizationType = UITextAutocapitalizationTypeNone;
    _passwordField.returnKeyType = UIReturnKeyGo;
    
    TTTableButton* loginButton = [TTTableButton itemWithText:@"Log In" delegate:self selector:@selector(authenticate)];
    
    TTTableTextItem* signup = [TTTableTextItem itemWithText:@"Sign up for a new account." URL:@"shoppley://signup"];
    
    _loginDataSource = [[TTSectionedDataSource dataSourceWithObjects:@"", _emailField, _passwordField, loginButton, @"", signup, nil] retain];
    self.dataSource = _loginDataSource;
    
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
    
    // Header
    UIView* headerView = [[[UIView alloc] initWithFrame:CGRectMake(0, 0, 320, 92)] autorelease];
    UIImageView* logoView = [[[UIImageView alloc] initWithFrame:CGRectMake(22, 10, 280, 72)] autorelease];
    logoView.image = [UIImage imageNamed:@"logo.png"];
    [headerView addSubview:logoView];
    self.tableView.tableHeaderView = headerView;
}

- (void)viewWillAppear:(BOOL)animated {
    [super viewWillAppear:animated];
    [self.navigationController setNavigationBarHidden:YES animated:YES];
}

#pragma mark Login

- (void)authenticate {
    if (!(TTIsStringWithAnyText(_emailField.text) && TTIsStringWithAnyText(_passwordField.text))) {
        UIAlertView *alert = [[UIAlertView alloc]
                              initWithTitle:@""
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
                              initWithTitle:@""
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
