//
//  CurrentOffersViewController.m
//  shoppleyClient
//
//  Created by yod on 6/13/11.
//  Copyright 2011 Shoppley. All rights reserved.
//

#import "CurrentOffersViewController.h"

#import "SLCurrentOffer.h"
#import "SLTableViewDataSource.h"

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

- (void)createModel {
    _offers = [[SLDataController sharedInstance] obtainCurrentOffersWithDelegate:self forcedDownload:NO];
    
    if (_offers) {
        TTDPRINT(@"%@", _offers);
        NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
        for (int i = 0; i < [_offers count]; i++) {
            SLCurrentOffer* offer = [_offers objectAtIndex:i];
            [items addObject:[SLCurrentOfferTableItem itemWithOffer:offer URL:nil]];
        }
        self.dataSource = [SLListDataSource dataSourceWithItems:items];
    } else {
        self.dataSource = [TTListDataSource dataSourceWithObjects:
                           [TTTableActivityItem itemWithText:@"Processing..."],
                           nil];
    }
}

@end
