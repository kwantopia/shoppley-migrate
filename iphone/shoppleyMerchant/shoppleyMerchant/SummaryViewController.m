//
//  SummaryViewController.m
//  shoppleyMerchant
//
//  Created by yod on 6/14/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "SummaryViewController.h"

#import "SLDataController.h"
#import "SLTableItem.h"
#import "SLTableViewDataSource.h"


@implementation SummaryViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.title = @"Summary";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_summary.png"] tag:0] autorelease];
        
        self.navigationItem.rightBarButtonItem = [[[UIBarButtonItem alloc] initWithBarButtonSystemItem:UIBarButtonSystemItemRefresh target:self action:@selector(createModel)] autorelease];
        
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
    self.dataSource = [TTListDataSource dataSourceWithObjects:[TTTableActivityItem itemWithText:@"Processing..."], nil];
    [self performSelectorInBackground:@selector(getSummary) withObject:self];
}

- (void)getSummaryDone:(NSDictionary*)result {
    self.dataSource = [SLSectionedDataSource dataSourceWithObjects:
                       @"Weekly Summary",
                       [SLRightValueTableItem itemWithText:@"# of offers" value:[NSString stringWithFormat:@"%@", [result objectForKey:@"num_offers"]]],
                       [SLRightValueTableItem itemWithText:@"# of people reached" value:[NSString stringWithFormat:@"%@", [result objectForKey:@"total_received"]]],
                       [SLRightValueTableItem itemWithText:@"# of people forwarded" value:[NSString stringWithFormat:@"%@", [result objectForKey:@"total_forwarded"]]],
                       [SLRightValueTableItem itemWithText:@"# of people redeemed" value:[NSString stringWithFormat:@"%@", [result objectForKey:@"total_redeemed"]]],
                       nil];
}

- (void)getSummaryFailed {
    self.dataSource = [TTListDataSource dataSourceWithObjects:[TTTableTextItem itemWithText:@"Please try again later."], nil];
}

- (void)getSummary {
    NSAutoreleasePool *pool = [[NSAutoreleasePool alloc] init];
    
    NSDictionary* result = [[SLDataController sharedInstance] getSummary];
    
    if (result != NULL) {
        [self performSelectorOnMainThread:@selector(getSummaryDone:) withObject:result waitUntilDone:NO];
    } else {
        UIAlertView *alert = [[[UIAlertView alloc]
                               initWithTitle:@""
                               message:[SLDataController sharedInstance].errorString
                               delegate:self
                               cancelButtonTitle:@"OK"
                               otherButtonTitles: nil] autorelease];
        [alert show];
        [self performSelectorOnMainThread:@selector(sendMoreOffersFailed) withObject:nil waitUntilDone:NO];
    }
    
    [pool release];
}

@end
