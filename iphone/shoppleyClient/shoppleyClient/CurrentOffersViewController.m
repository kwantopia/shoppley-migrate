//
//  CurrentOffersViewController.m
//  shoppleyClient
//
//  Created by yod on 6/13/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "CurrentOffersViewController.h"

@implementation CurrentOffersViewController

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil {
    if ((self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil])) {
        self.title = @"Current Offers";
        self.tabBarItem = [[[UITabBarItem alloc] initWithTitle:self.title image:[UIImage imageNamed:@"tab_current_offers.png"] tag:0] autorelease];
        
        self.tableViewStyle = UITableViewStylePlain;
        self.variableHeightRows = YES;
    }
    return self;
}

- (void)dealloc {
    [super dealloc];
}

- (void)createModel {
    NSArray* offers = [[SLDataController sharedInstance] obtainCurrentOffersWithDelegate:self forcedDownload:NO];
    TTDPRINT(@"%@", offers);
    
    self.dataSource = [TTSectionedDataSource dataSourceWithObjects:
                       @"",
                       [TTTableTextItem itemWithText:@"Offer" URL:@"http://www.mit.edu"],
                       [TTTableTextItem itemWithText:@"Offer" URL:@"http://www.mit.edu"],
                       nil
                       ];
}

- (void)didFinishDownload {
    [self reload];
}

- (void)didFailDownload {
    TTDPRINT(@"failed");
}

@end
