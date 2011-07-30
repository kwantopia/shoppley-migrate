//
//  IWantViewController.m
//  shoppleyClient
//
//  Created by yod on 7/29/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "IWantViewController.h"

#import "SLDataController.h"

@implementation IWantViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.tableViewStyle = UITableViewStyleGrouped;
        self.autoresizesForKeyboard = NO;
        self.variableHeightRows = YES;
        self.tableView.scrollEnabled = NO;
        
        self.title = @"I Want";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_settings.png"] tag:0] autorelease];
        
        self.navigationItem.leftBarButtonItem = [[[UIBarButtonItem alloc] initWithTitle:@"Cancel" style:UIBarButtonItemStyleBordered target:self action:@selector(cancel)] autorelease];
        
        _textEditor = [[TTTextEditor alloc] init];
        _textEditor.font = TTSTYLEVAR(font);
        _textEditor.autoresizesToText = NO;
        _textEditor.minNumberOfLines = 5;
        _textEditor.placeholder = @"Tell us the type of offers, brands or stores you want.";
        
        TTButton* button = [TTButton buttonWithStyle:@"greenButton:" title:@"Send"];
        [button addTarget:self action:@selector(submit) forControlEvents:UIControlEventTouchUpInside];
        button.enabled = YES;
        [button sizeToFit];
        button.frame = CGRectMake(10, 10, self.view.frame.size.width - 20, button.frame.size.height);
        
        _footerView = [[UIView alloc] initWithFrame:CGRectMake(0, 0, self.view.frame.size.width, button.frame.size.height + 10)];
        [_footerView addSubview:button];
    }
    return self;
}


- (void)dealloc {
    TT_RELEASE_SAFELY(_textEditor);
    TT_RELEASE_SAFELY(_footerView);
    [super dealloc];
}

- (void)createModel {
    self.tableView.tableFooterView = _footerView;
    self.dataSource = [TTListDataSource dataSourceWithObjects:_textEditor, nil];
}

- (void)cancel {
    _textEditor.text = @"";
    [_textEditor resignFirstResponder];
}

- (void)submit {
    if (!TTIsStringWithAnyText(_textEditor.text)) {
        return;
    }
    
    [_textEditor resignFirstResponder];
    self.dataSource = [TTListDataSource dataSourceWithObjects:[TTTableActivityItem itemWithText:@"Processing..."], nil];
    self.tableView.tableFooterView = NULL;
    
    if ([[SLDataController sharedInstance] sendIWant:_textEditor.text]) {
        _textEditor.text = @"";
        
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"" message:@"Successfully Sent" delegate:self cancelButtonTitle:@"OK" otherButtonTitles: nil] autorelease];
        [alert show];
        
    } else {
        UIAlertView *alert = [[[UIAlertView alloc] initWithTitle:@"Connection Error" message:@"Please try again later." delegate:self cancelButtonTitle:@"OK" otherButtonTitles: nil] autorelease];
        [alert show];
    }
    
    [self createModel];
}

@end
