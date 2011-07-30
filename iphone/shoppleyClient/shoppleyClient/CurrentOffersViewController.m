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
     NSArray* offers = [[SLDataController sharedInstance] obtainCurrentOffersWithDelegate:self forcedDownload:NO];
    
    if (offers) {
        NSArray* forwardedOffers = [[SLDataController sharedInstance] obtainForwardedOffers];
        _offersSections = [[NSArray arrayWithObjects:forwardedOffers, offers, nil] retain];
        
        
        NSMutableArray* items = [[[NSMutableArray alloc] init] autorelease];
        for (int i = 0; i < [offers count]; i++) {
            SLCurrentOffer* offer = [offers objectAtIndex:i];
            [items addObject:[SLCurrentOfferTableItem itemWithOffer:offer URL:nil]];
        }
        
        if ([items count] == 0) {
            [items addObject:[TTTableTextItem itemWithText:@"Sorry, we don't have any offers near you." URL:nil]];
        }
        
        NSMutableArray* forwardedItems = [[[NSMutableArray alloc] init] autorelease];
        for (int i = 0; i < [forwardedOffers count]; i++) {
            SLCurrentOffer* offer = [forwardedOffers objectAtIndex:i];
            [forwardedItems addObject:[SLCurrentOfferTableItem itemWithOffer:offer URL:nil]];
        }
        
        NSArray* dataSourcesItems = [NSArray arrayWithObjects:forwardedItems, items, nil];
        NSArray* dataSourcesSections;
        
        if ([forwardedItems count] > 0) {
            dataSourcesSections = [NSArray arrayWithObjects:@"Forwarded to you", @"Near you", nil];
        } else {
            dataSourcesSections = [NSArray arrayWithObjects:@"", @"", nil];
        }
        
        self.dataSource = [SLSectionedDataSource dataSourceWithItems:dataSourcesItems sections:dataSourcesSections];
    } else {
        self.dataSource = [TTListDataSource dataSourceWithObjects:
                           [TTTableActivityItem itemWithText:@"Processing..."],
                           nil];
    }
}

@end
