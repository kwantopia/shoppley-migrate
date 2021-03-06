//
//  SettingsViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/19/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SettingsViewController.h"

#import "SLDataController.h"

@implementation SettingsViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.title = @"Settings";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_settings.png"] tag:0] autorelease];
        
        self.tableViewStyle = UITableViewStyleGrouped;
        self.variableHeightRows = YES;
        self.tableView.scrollEnabled = NO;
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
}

- (void)createModel {
    NSUserDefaults *defaults = [NSUserDefaults standardUserDefaults];
    NSString *email = [defaults stringForKey:@"email"];
    
    self.dataSource = [TTSectionedDataSource dataSourceWithObjects:
                       @"",
                       [TTTableSummaryItem itemWithText:email URL:nil],
                       [TTTableButton itemWithText:@"Log Out" URL:nil],
                       nil
                       ];
}

- (void)didSelectObject:(id)object atIndexPath:(NSIndexPath*)indexPath {
    [super didSelectObject:object atIndexPath:indexPath];
    if (indexPath.section == 0 && indexPath.row == 1) {
        [self logout];
    }
}

- (void)logout {
    [[SLDataController sharedInstance] logout];
}

@end
